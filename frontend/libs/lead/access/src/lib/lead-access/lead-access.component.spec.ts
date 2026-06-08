import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadAccessComponent } from './lead-access.component';

describe('LeadAccessComponent', () => {
  let component: LeadAccessComponent;
  let fixture: ComponentFixture<LeadAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
