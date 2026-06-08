import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstDataAccessComponent } from './asst-data-access.component';

describe('AsstDataAccessComponent', () => {
  let component: AsstDataAccessComponent;
  let fixture: ComponentFixture<AsstDataAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstDataAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstDataAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
