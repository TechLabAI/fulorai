import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstAccessComponent } from './asst-access.component';

describe('AsstAccessComponent', () => {
  let component: AsstAccessComponent;
  let fixture: ComponentFixture<AsstAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
