import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AsstStylesComponent } from './asst-styles.component';

describe('AsstStylesComponent', () => {
  let component: AsstStylesComponent;
  let fixture: ComponentFixture<AsstStylesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsstStylesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(AsstStylesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
